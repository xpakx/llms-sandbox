package main

import (
	"bufio"
	"flag"
	"io"
	"log"
	"os"
	"os/exec"
	"strings"
)

func main() {
	iFlag := flag.Bool("i", false, "Interactive mode")
	flag.Parse()

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

func sendMessage(msg string) {
	log.Println(msg)
}
