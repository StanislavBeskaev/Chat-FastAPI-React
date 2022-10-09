import React, {useEffect, useRef} from 'react'
import {Button, Form, InputGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'
import EmojiPicker from './EmojiPicker'

import messagesStore from '../../stores/messagesStore'


const STOP_TYPING_DELAY = 3_000

const TextForm = ({sendTextMessage, sendStartTyping, sendStopTyping}) => {
  const {selectedChatText, selectedChatTyping} = messagesStore
  const textInputRef = useRef(null)

  useEffect(() => {
    messagesStore.setTextInputRef(textInputRef)
    textInputRef.current.focus()
  }, [])

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
    messagesStore.readAllMessagesInWaitList()
  }

  return (
    <div className="d-flex">
      <EmojiPicker/>
      <Form onSubmit={handleSubmit} className="flex-grow-1">
        <Form.Group className="m-2">
          <InputGroup>
            <Form.Control
              as="textarea"
              required
              value={selectedChatText}
              onChange={e => messagesStore.setSelectedChatText(e.target.value)}
              onKeyPress={handleKeyPress}
              style={{height: '30px', resize: 'none'}}
              ref={textInputRef}
            />
            <Button type="submit">Отправить</Button>
          </InputGroup>
        </Form.Group>
      </Form>
    </div>

  )
}

export default observer(TextForm)