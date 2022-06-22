import React from 'react'
import {observer} from 'mobx-react-lite'
import {Alert, Button, Form, Modal} from 'react-bootstrap'

import ValueInput from '../UI/Inputs/ValueInput'
import changeChatNameModalStore from '../../stores/modals/changeChatNameModalStore'


const ChangeChatNameModal = () => {
  const {error, name, success, previousName} = changeChatNameModalStore

  const changeName = e => {
    changeChatNameModalStore.setName(e.target.value)
  }

  const handleSubmit = async e => {
    e.preventDefault()
    await changeChatNameModalStore.changeChatName()
  }

  return (
    <>
      <Modal.Header>Изменение названия чата "{previousName}"</Modal.Header>
      <Modal.Body>
        {
          error
            ? <Alert variant="danger" className="mt-3">{error}</Alert>
            : null
        }
        <Form onSubmit={handleSubmit}>
          <div className="d-flex flex-column">
            <ValueInput
              label="Новое название"
              type="text"
              required={true}
              value={name}
              onChange={changeName}
            />
            <div className="mt-4 align-self-center">
              {
                success
                  ? <Alert variant="success">Название чата изменено</Alert>
                  : <Button type="submit" variant="primary">Изменить</Button>
              }
            </div>
          </div>
        </Form>
      </Modal.Body>
    </>
  )
}

export default observer(ChangeChatNameModal)