package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
)

func main() {
	w := websocket_service{};
	p := tea.NewProgram(initialModel(&w))
	w.SetProgram(p)
	w.ConnectWS()
	go w.Run()
	w.Connect()
	w.Subscribe()

	defer func() {
		if w.Connection != nil {
			if err := w.Connection.Close(); err != nil {
				fmt.Println("error closing WebSocket connection:", err)
			} else {
				fmt.Println("closed WebSocket connection")
			}
		} else {
			fmt.Println("No WebSocket connection")
		}
	}()
	
	if _, err := p.Run(); err != nil {
		fmt.Printf("error: %v", err)
		os.Exit(1)
	}
}

type Message struct {
	Content       string    `json:"content"`
	Timestamp     string    `json:"timestamp"`
	Id            string    `json:"id"`
	Username      string    `json:"username"`
}

type MessageItem struct { 
	Type          string    `json:"type"`
	Message       Message   `json:"message"`
}
