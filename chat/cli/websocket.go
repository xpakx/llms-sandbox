package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"regexp"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	websocket "github.com/gorilla/websocket"
)


type websocket_service struct {
	program *tea.Program
	Connection *websocket.Conn
}

func (m *websocket_service) SetProgram(program *tea.Program) {
	m.program = program
}


func (ws *websocket_service) ConnectWS() {
	url := "ws://localhost:8080/ws/websocket"

	c, _, err := websocket.DefaultDialer.Dial(url, nil)
	if err != nil {
		log.Fatal("dial:", err)
	}

	ws.Connection = c
}

func (ws *websocket_service) Connect() {
	connectMessage := fmt.Sprintf("CONNECT\naccept-version:%s\nheart-beat:%s\n\n\000", "1.2,1.1,1.0", "20000,0")
	err := ws.Connection.WriteMessage(websocket.TextMessage, []byte(connectMessage))
	if err != nil {
		log.Fatal("write:", err)
	}
}


func (ws *websocket_service) Subscribe() {
	topic := "/topic/chat";
	subscribeMessage := fmt.Sprintf("SUBSCRIBE\nid:sub-0\ndestination:%s\n\n\000", topic);
	err := ws.Connection.WriteMessage(websocket.TextMessage, []byte(subscribeMessage))
	if err != nil {
		log.Println("write:", err)
		return
	}
}

func (ws *websocket_service) Run() {
	done := make(chan struct{})
	go func() {
		defer close(done)
		for {
			select {
			case <-done:
				fmt.Println("end")
				return
			default:
				_, message, err := ws.Connection.ReadMessage()
				if err != nil {
					log.Println("read:", err)
					return
				}
				ws.handleMessage(string(message))
			}
		}
	}()

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	select {
	case <-interrupt:
		log.Println("interrupt")
	}

	err := ws.Connection.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
	if err != nil {
		log.Println("write close:", err)
		return
	}
	select {
	case <-done:
	case <-time.After(time.Second):
	}

}

type ChannelMsg struct {
	messages []MessageItem
}

func (m websocket_service) handleMessage(rawMessage string) {
    destination, err := extractDestination(rawMessage);
    if err == nil {
	    switch destination {
	    case "chat":
		    var data []MessageItem
		    var body, errb = extractBody(rawMessage)
		    if errb != nil {
			    return
		    }
		    if err := json.Unmarshal([]byte(body), &data); err == nil {
			    m.program.Send(ChannelMsg{messages: data })
		    }
	    }
    }
}

func extractDestination(message string) (string, error) {
    pattern := `destination:/topic/([a-z]+)`
    re := regexp.MustCompile(pattern)
    matches := re.FindStringSubmatch(message)
    if len(matches) < 2 {
        return "", fmt.Errorf("destination not found in message")
    }
    return matches[1], nil
}

func extractBody(message string) (string, error) {
    start := strings.Index(message, "\n\n")
    if start == -1 {
        return "", fmt.Errorf("start of body not found in message")
    }
    start += 2 

    end := strings.Index(message, "\000")
    if end == -1 {
        return "", fmt.Errorf("end of body not found in message")
    }

    return message[start:end], nil
}
