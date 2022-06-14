import React, {useState} from 'react'
import {Button, Form, InputGroup} from 'react-bootstrap'

const TextForm = ({sendText, sendTypingStart}) => {
  const [text, setText] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    send()
  }

  function handleKeyPress(e) {
    sendTypingStart()
    if (e.key !== 'Enter') return

    e.preventDefault()
    send()
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