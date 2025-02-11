package main

import (
	"os"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"golang.org/x/term"
)

var (
	subtle    = lipgloss.AdaptiveColor{Light: "#D9DCCF", Dark: "#383838"}
	highlight = lipgloss.AdaptiveColor{Light: "#874BFD", Dark: "#7D56F4"}
	special   = lipgloss.AdaptiveColor{Light: "#43BF6D", Dark: "#73F59F"}
	yellow   = lipgloss.Color("#F4D03F")
	red   = lipgloss.Color("#E74C3C")

	border = lipgloss.Border{
		Top:         "─",
		Bottom:      "─",
		Left:        "│",
		Right:       "│",
		TopLeft:     "╭",
		TopRight:    "╮",
		BottomLeft:  "╰ ",
		BottomRight: "╯",
	}

	// Status Bar.
	logoStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FFFDF5")).
			Background(lipgloss.Color("#6124DF")).
			Padding(0, 1)

	descriptionBarStyle = lipgloss.NewStyle().
			Foreground(lipgloss.AdaptiveColor{Light: "#343433", Dark: "#C1C6B2"}).
			Background(lipgloss.AdaptiveColor{Light: "#D9DCCF", Dark: "#353533"})

	modeStyle = lipgloss.NewStyle().
			Inherit(descriptionBarStyle).
			Foreground(lipgloss.Color("#FFFDF5")).
			Background(lipgloss.Color("#0F5F87")).
			Padding(0, 1)

	statusStyle = modeStyle.
			Background(lipgloss.Color("#A550DF")).
			Align(lipgloss.Left).
			MarginRight(1)

	onlineStyle = statusStyle.
			SetString("⍟").
			Foreground(special).
			String()
	idleStyle = statusStyle.
			SetString("◷").
			Foreground(yellow).
			String()
	doNotDisturbStyle = statusStyle.
			SetString("⊗").
			Foreground(red).
			String()
	invisibleStyle = statusStyle.
			SetString("👻").
			PaddingRight(1).
			String()


	statusText = lipgloss.NewStyle().Inherit(descriptionBarStyle)

	// Chat
	input = lipgloss.NewStyle().
		Border(border, true).
		BorderForeground(subtle).
		MarginTop(1).
		Padding(0, 1)
	
	nameStyle = lipgloss.NewStyle().
		Foreground(highlight).
		MarginRight(5)
	myNameStyle = nameStyle.
		Foreground(special)
	dateStyle = lipgloss.NewStyle().
		Foreground(subtle)

	message = func(name string, date string, content string, me bool, width int) string {
		var nameR = ""
		if (me) {
			nameR = myNameStyle.Render(name) 
		} else {
			nameR = nameStyle.Render(name) 
		}
		var dateR = dateStyle.Render(date)

		gap := strings.Repeat(" ", max(0, width-lipgloss.Width(nameR)-lipgloss.Width(dateR)))
		header := nameR + gap + dateR
		return  lipgloss.JoinVertical(lipgloss.Top,
				header,
				lipgloss.NewStyle().Width(width).Render(content),
			)
	}
	
	docStyle = lipgloss.NewStyle().Padding(1, 2, 1, 2)
)

func draw(m model) (string) {
	messages := m.messages

	physicalWidth, _, _ := term.GetSize(int(os.Stdout.Fd()))
	doc := strings.Builder{}

	var renderedMessages []string
	for _, msg := range messages {
		if msg.Type == "Message" {
			renderedMessages = append(
				renderedMessages, 
				message(msg.Message.Username, msg.Message.Timestamp, msg.Message.Content, msg.Message.Username == "me", m.width))
		}
	}

	msgs := lipgloss.
		NewStyle().
		MaxHeight(m.height - 4).
		Height(m.height - 4).
		Render(m.viewport.View())
	doc.WriteString(msgs)
	doc.WriteString("\n")

	// Status bar 
	{
		w := lipgloss.Width

		modeIndicator := modeStyle.Render("INSERT")
		nameContainer := logoStyle.Render("🧶 AI")
		description := statusText.
			Width(m.width - w(modeIndicator) - w(nameContainer)).
			Render("Desc")

		bar := lipgloss.JoinHorizontal(lipgloss.Top,
			modeIndicator,
			description,
			nameContainer,
		)

		doc.WriteString(descriptionBarStyle.Width(m.width).Render(bar))
	}

	if physicalWidth > 0 {
		docStyle = docStyle.MaxWidth(physicalWidth)
	}

	return docStyle.Render(doc.String())
}
