import React from 'react'
import {Alert, Button, Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import addContactModalStore from '../../stores/modals/addContactModalStore'
import contactStore from '../../stores/contactStore'

import Loader from '../UI/Loader/Loader'
import UserAvatar from '../Avatars/UserAvatar'


const AddContactModal = () => {
  const {loading, login, error, successAdd} = addContactModalStore

  const loginAlreadyInContacts = contactStore.hasLogin(login)
  let name
  let surname

  if (loginAlreadyInContacts) {
    const contactLogin = contactStore.findContactByLogin(login)
    name = contactLogin.name
    surname = contactLogin.surname
  } else {
    name = addContactModalStore?.userInfo?.name
    surname = addContactModalStore?.userInfo?.surname
  }

  const addContact = async () => {
    await addContactModalStore.handleAddContact()
  }

  if (loading) {
    return <>
      <Modal.Header closeButton>Пользователь {login}</Modal.Header>
      <Modal.Body>
        <Loader/>
      </Modal.Body>
    </>
  }

  return (
    <>
      <Modal.Header closeButton>Пользователь {login}</Modal.Header>
      <Modal.Body>
        <div className="d-flex flex-column">
          <div className="d-flex flex-row justify-content-around">
            <UserAvatar login={login} size="md"/>
            <ul className="align-self-start">
              <li>Имя: {name}</li>
              <li>Фамилия: {surname}</li>
            </ul>
          </div>
          <div className="mt-4 align-self-center">
            {
              successAdd
                ? <Alert variant="success">Контакт успешно добавлен</Alert>
                : <div>
                  {
                    loginAlreadyInContacts
                      ? <Alert variant="info">Пользователь уже есть в контактах</Alert>
                      : <div>
                        <Button onClick={addContact}>Добавить в контакты</Button>
                        {error && <Alert key="danger" variant="danger" className="mt-3">{error}</Alert>}
                      </div>
                  }
                </div>
            }
          </div>
        </div>
      </Modal.Body>
    </>
  )
}

export default observer(AddContactModal)