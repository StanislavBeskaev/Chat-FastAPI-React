import React, {useState, useEffect} from 'react'
import {Button, Form, InputGroup} from 'react-bootstrap'

const STOP_TYPING_DELAY = 10000

const TextForm = ({sendText, sendStartTyping, sendStopTyping}) => {
  // TODO нужно сохранять текст в store, что бы менялся при переключении чатов
  const [text, setText] = useState('')
  const [typing, setTyping] = useState(false)

  useEffect(() => {
    const stopTypingTimeout = setTimeout(()=> {
      if (typing) {
        setTyping(false)
        sendStopTyping()
      }
    }, STOP_TYPING_DELAY)

    return () => clearTimeout(stopTypingTimeout)
  }, [text])

  const handleSubmit = (e) => {
    e.preventDefault()
    send()
  }

  function handleKeyPress(e) {
    if (!typing) {
      setTyping(true)
      sendStartTyping()
    }
    if (e.key !== 'Enter') return

    e.preventDefault()
    send()
    sendStopTyping()
    setTyping(false)
  }

  const send = () => {
    if (!text) return
    sendText(text)
    setText('')
  }

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="m-2">
        <InputGroup>
          <Form.Control
            as="textarea"
            required
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyPress={handleKeyPress}
            style={{height: '30px', resize: 'none'}}
          />
          <Button type="submit">Отправить</Button>
        </InputGroup>
      </Form.Group>
    </Form>
  )
}

export default TextForm