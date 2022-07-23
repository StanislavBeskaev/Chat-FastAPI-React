import React from 'react'
import {Form, Modal, Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messageContextMenuStore from '../../stores/messageContextMenuStore'

const MessageEditModal = () => {
  const {messageText} = messageContextMenuStore

  const changeText = e => {
    messageContextMenuStore.setMessageText(e.target.value)
  }

  const handleKeyPress = e => {
    if (e.key === 'Enter') {
      e.preventDefault()
      return
    }
  }

  // TODO проверка, что текст не пустой
  const submitChange = e => {
    e.preventDefault()
    messageContextMenuStore.changeMessageText()
    messageContextMenuStore.closeMessageEditModal()
    alert('Тут будет изменение сообщения')
  }

  return (
    <>
      <Modal.Header closeButton>Редактирование сообщения</Modal.Header>
      <Modal.Body>
        <Form className="d-flex flex-column gap-2">
          <Form.Control
            as="textarea"
            placeholder="Текст сообщения"
            value={messageText}
            onChange={changeText}
            onKeyPress={handleKeyPress}
          />
          <Button
            onClick={submitChange}
            className="align-self-center"
            disabled={messageText?.length === 0}
          >
            Изменить
          </Button>
        </Form>
      </Modal.Body>
    </>
  )
}

export default observer(MessageEditModal)