import React from 'react';
import {Alert, Button, Form, Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import contactModalStore from '../../stores/modals/contactModalStore'
import Loader from '../UI/Loader/Loader'
import UserAvatar from '../Avatars/UserAvatar'


const ContactModal = () => {
  const {loading, login, name, surname, changed} = contactModalStore

  if (loading) {
    return <>
      <Modal.Header closeButton> Пользователь {login}</Modal.Header>
      <Modal.Body>
        <Loader />
      </Modal.Body>
    </>
  }

  const changeName = e => {
    contactModalStore.setName(e.target.value)
  }

  const changeSurname = e => {
    contactModalStore.setSurname(e.target.value)
  }

  const changeContact = async e => {
    e.preventDefault()
    await contactModalStore.changeContact()
  }

  return (
    <>
      <Modal.Header closeButton> Пользователь {login}</Modal.Header>
      <Modal.Body>
        <div className="d-flex justify-content-around">
          <UserAvatar login={login} size="md" />
          <Form className="d-flex flex-column gap-2">
            <Form.Control
              placeholder="Имя"
              value={name}
              onChange={changeName}
            />
            <Form.Control
              placeholder="Фамилия"
              value={surname}
              onChange={changeSurname}
            />
            <Button
              className="align-self-end"
              onClick={changeContact}
            >Изменить</Button>
          </Form>
        </div>
        {
          changed
            ? <Alert variant="success" className="mt-3">Данные контакта изменены</Alert>
            : null
        }
      </Modal.Body>
    </>
  )
}

export default observer(ContactModal)
