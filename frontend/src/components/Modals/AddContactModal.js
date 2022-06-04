import React from 'react'
import {Alert, Button, Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import addContactModalStore from '../../stores/modals/addContactModalStore'

import Loader from '../UI/Loader/Loader'
import Avatar from '../Avatars/Avatar'
import contactStore from '../../stores/contactStore'


const AddContactModal = () => {
  const {loading, login, error, successAdd} = addContactModalStore

  const loginAlreadyInContacts = contactStore.hasLogin(login)

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

  //TODO если пользователь есть в контактах, то name и surname брать из контакта

  return (
    <>
      <Modal.Header closeButton>Пользователь {login}</Modal.Header>
      <Modal.Body>
        <div className="d-flex flex-column">
          <div className="d-flex flex-row justify-content-around">
            <Avatar
              fileName={addContactModalStore?.userInfo?.avatar_file}
              size="md"
            />
            <ul className="align-self-start">
              <li>Имя: {addContactModalStore?.userInfo?.name}</li>
              <li>Фамилия: {addContactModalStore?.userInfo?.surname}</li>
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