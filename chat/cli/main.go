package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
)

func main() {
	iFlag := flag.Bool("i", false, "Interactive mode")
	flag.Parse()

	// subprograms
	if len(flag.Args()) > 0 {
		subcommand := flag.Arg(0)
		switch subcommand {
		case "print":
			printCmd := flag.NewFlagSet("print", flag.ExitOnError)
			verboseFlag := printCmd.Bool("v", false, "Verbose mode")
			printCmd.Parse(flag.Args()[1:])

			printSubProgram(*verboseFlag)
			return
		}
	}

	if *iFlag {
		interactive_main()
	} else if isInputFromPipe() {
		pipe()
	} else if len(flag.Args()) > 0 {
		raw_message(flag.Args())
	} else {
		editor()
	}
}


func editor() {
	tmpFile, err := os.CreateTemp("", "myTempFile")
	if err != nil {
		log.Fatal("couldn't make a temp file")
	}
	defer os.Remove(tmpFile.Name())

	data := []byte("")
	if err := os.WriteFile(tmpFile.Name(), data, 0644); err != nil {
		log.Fatal("writing to temp file failed")
	}

	cmd := exec.Command("nvim", tmpFile.Name())
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	if err := cmd.Run(); err != nil {
		log.Println("Cancelled")
		return
	}

	content, err := os.ReadFile(tmpFile.Name())
	if err != nil {
		log.Fatal("couldn't read temp file")
	}

	sendMessage(string(content))
}

func isInputFromPipe() bool {
	fileInfo, _ := os.Stdin.Stat()
	return (fileInfo.Mode() & os.ModeCharDevice) == 0
}

func pipe() {
	reader := bufio.NewReader(os.Stdin)
	var input []byte
	for {
		line, err := reader.ReadBytes('\n')
		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatal("Error reading from stdin:", err)
		}
		input = append(input, line...)
	}
	sendMessage(string(input))
}

func raw_message(args []string) {
	var builder strings.Builder
	for _, arg := range args {
		builder.WriteString(arg)
	}
	result := builder.String()
	sendMessage(result)
}


type MessageDto struct { 
	Content          string    `json:"content"`
}

func sendMessage(msg string) {
	log.Println(msg)
	message := MessageDto{
		Content: msg,
	}
	jsonData, err := json.Marshal(message)
	if err != nil {
		log.Fatalf("error marshalling message: %v", err)
	}

	url := "http://localhost:8000/send/chat"

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Fatalf("error sending request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("unexpected status code: %d", resp.StatusCode)
	}

	log.Println("Message sent successfully")
}

func printSubProgram(verbose bool) {
	url := "http://localhost:8000/chat/0"

	resp, err := http.Get(url)
	if err != nil {
		log.Printf("Error fetching data: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Error reading response body: %v\n", err)
		return
	}

	var message MessageItem
	err = json.Unmarshal(body, &message)
	if err != nil {
		log.Printf("Error unmarshaling JSON: %v\n", err)
		return
	}

	if verbose {
		fmt.Printf("Verbose Output:\n")
		fmt.Printf("ID: %d\n", message.Message.Id)
		fmt.Printf("Type: %d\n", message.Type)
		fmt.Printf("Author: %s\n", message.Message.Username)
		fmt.Printf("Time: %s\n", message.Message.Timestamp)
		fmt.Printf("Content: %s\n", message.Message.Content)
	} else {
		fmt.Printf(message.Message.Content)
	}
}
