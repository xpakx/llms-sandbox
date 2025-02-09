package main

import (
	"flag"
	"log"
	"os"
	"os/exec"
)

func main() {
	iFlag := flag.Bool("i", false, "Interactive mode")
	flag.Parse()

	if *iFlag {
		interactive_main()
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

	log.Println(string(content))
}
