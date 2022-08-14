import React, {useRef, useEffect} from 'react'
import {Form, Modal, Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messageContextMenuStore from '../../stores/messageContextMenuStore'


const MessageEditModal = () => {
  const {messageText, beforeChangeMessageText} = messageContextMenuStore
  const inputRef = useRef()

  useEffect(() => {
    if (inputRef.current) {
      // что бы при появлении был курсор в конце текста
      inputRef.current.focus()
      inputRef.current.setSelectionRange(messageText.length, messageText.length)
    }
  }, [])

  const changeText = e => {
    messageContextMenuStore.setMessageText(e.target.value)
  }

  const handleKeyPress = async e => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (messageText !== beforeChangeMessageText) await submitChange()
    }
  }

  const submitChange = async () => {
    if (messageText.length === 0) return

    await messageContextMenuStore.changeMessageText()
  }

  return (
    <>
      <Modal.Header closeButton>Редактирование сообщения</Modal.Header>
      <Modal.Body>
        <Form className="d-flex flex-column gap-2">
          <Form.Control
            ref={inputRef}
            as="textarea"
            placeholder="Текст сообщения"
            value={messageText}
            onChange={changeText}
            onKeyPress={handleKeyPress}
          />
          <Button
            onClick={submitChange}
            className="align-self-center"
            disabled={messageText?.length === 0 || messageText === beforeChangeMessageText}
          >
            Изменить
          </Button>
        </Form>
      </Modal.Body>
    </>
  )
}

export default observer(MessageEditModal)