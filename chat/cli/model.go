package main

import (
	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type model struct {
    messages           []MessageItem   
    websocket          *websocket_service
    viewport           viewport.Model
    width              int
    height             int
}

func initialModel(websocket *websocket_service) model {
	newViewport := viewport.New(30, 15)

	return model{
		messages: []MessageItem{},
		websocket: websocket,
		viewport: newViewport,
	}
}

func (m *model) UpdateViewport() {
	chatWidth := m.width - 4;
	var renderedMessages []string
	for _, msg := range m.messages {
		if msg.Type == "Message" {
			renderedMessages = append(
				renderedMessages, 
				message(msg.Message.Username, msg.Message.Timestamp, msg.Message.Content, msg.Message.Username == "me", chatWidth))
		}
	}

	messageContainer := lipgloss.JoinVertical(lipgloss.Top, renderedMessages...)
	m.viewport.Width = m.width - 2;
	m.viewport.Height = m.height - 4;
	m.viewport.SetContent(messageContainer)
}

func (m model) Init() tea.Cmd {
    return textarea.Blink
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
		    return m, tea.Quit
		}
    case ChannelMsg:
	    m.messages = append(m.messages, msg.messages...)
	    m.UpdateViewport()
	    m.viewport.GotoBottom()
    case tea.WindowSizeMsg:
	    m.width = msg.Width
	    m.height = msg.Height
	    m.UpdateViewport()
    }

    return m, nil
}

func (m model) View() string {
    return draw(m)
}
