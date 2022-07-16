import React, {useEffect} from 'react'
import {Button, Form, InputGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../stores/messagesStore'


const STOP_TYPING_DELAY = 5_000

const TextForm = ({sendTextMessage, sendStartTyping, sendStopTyping}) => {
  const {selectedChatText, selectedChatTyping} = messagesStore

  useEffect(() => {
    const stopTypingTimeout = setTimeout(()=> {
      if (selectedChatTyping) {
        messagesStore.setSelectedChatTyping(false)
        sendStopTyping()
      }
    }, STOP_TYPING_DELAY)

    return () => clearTimeout(stopTypingTimeout)
  }, [selectedChatText])

  const handleSubmit = (e) => {
    e.preventDefault()
    send()
  }

  function handleKeyPress(e) {
    if (!selectedChatTyping) {
      messagesStore.setSelectedChatTyping(true)
      sendStartTyping()
    }
    if (e.key !== 'Enter') return

    e.preventDefault()
    send()
  }

  const send = () => {
    if (!selectedChatText) return
    sendTextMessage(selectedChatText)
    messagesStore.setSelectedChatText('')
    sendStopTyping()
    messagesStore.setSelectedChatTyping(false)
  }

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="m-2">
        <InputGroup>
          <Form.Control
            as="textarea"
            required
            value={selectedChatText}
            onChange={e => messagesStore.setSelectedChatText(e.target.value)}
            onKeyPress={handleKeyPress}
            style={{height: '30px', resize: 'none'}}
          />
          <Button type="submit">Отправить</Button>
        </InputGroup>
      </Form.Group>
    </Form>
  )
}

export default observer(TextForm)