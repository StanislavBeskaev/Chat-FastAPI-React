import React from 'react'
import {observer} from 'mobx-react-lite'
import {Alert, Button, Form, Modal} from 'react-bootstrap'

import contactStore from '../../stores/contactStore'
import ValueInput from '../UI/Inputs/ValueInput'
import newChatModalStore from '../../stores/modals/newChatModalStore'


const NewChatModal = () => {
  const {name, error, logins, success} = newChatModalStore

  async function handleSubmit(e) {
    e.preventDefault()
    await newChatModalStore.createNewChat()
  }

  function handleCheckboxChange(login) {
    newChatModalStore.toggleLogin(login)
  }

  const changeName = e => {
    newChatModalStore.setName(e.target.value)
  }

  return (
    <>
      <Modal.Header closeButton className="fs-5">Создание нового чата</Modal.Header>
      <Modal.Body>
        {
          error
            ? <Alert variant="danger" className="mt-3">{error}</Alert>
            : null
        }
        <Form onSubmit={handleSubmit}>
          <div className="d-flex flex-column">
            <ValueInput
              label="Название"
              type="text"
              required={true}
              value={name}
              onChange={changeName}
            />
            <div className="m-1 fs-5">Участники:</div>
            <div className="d-flex gap-3 ms-3 mt-2 flex-wrap">
              {contactStore.contacts.map(contact => (
                <Form.Group controlId={contact.login} key={contact.login}>
                  <Form.Check
                    type="checkbox"
                    value={logins.includes(contact.login)}
                    label={contact.login}
                    onChange={() => handleCheckboxChange(contact.login)}
                  />
                </Form.Group>
              ))}
            </div>
            <div className="mt-4 align-self-center">
              {
                success
                  ? <Alert variant="success">Чат успешно создан</Alert>
                  : <Button type="submit" variant="primary"> Создать </Button>
              }
            </div>
          </div>
        </Form>
      </Modal.Body>
    </>
  )
}

export default observer(NewChatModal)