import React, {useEffect, useState} from 'react'
import {Alert, Button, Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import addContactModalStore from '../../stores/modals/addContactModalStore'

import Loader from '../UI/Loader/Loader'
import Avatar from '../Avatars/Avatar'
import contactStore from '../../stores/contactStore'


const AddContactModal = () => {
  const [loading, setLoading] = useState(true)
  const {login} = addContactModalStore
  const {error} = contactStore

  useEffect(() => {
    addContactModalStore.loadUserInfo()
      .catch(e => console.log(`Не удалось загрузить информацию о пользователе: ${login}`, e))
      .finally(() => setLoading(false))
  }, [] )

  const addContact = async () => {
    await contactStore.addContact(login)
  }

  // TODO нужна проверка, есть ли пользователь уже в контактах
  //  если есть, то не показывать кнопку добавления
  return (
    <>
      <Modal.Header closeButton>Пользователь {login}</Modal.Header>
      <Modal.Body>
        {
          loading
          ? <Loader />
          : <div className="d-flex flex-column">
            <div className="d-flex flex-row justify-content-around">
              <ul className="align-self-start">
                <li>Имя: {addContactModalStore.userInfo.name}</li>
                <li>Фамилия: {addContactModalStore.userInfo.surname}</li>
              </ul>
              <Avatar
                fileName={addContactModalStore.userInfo.avatar_file}
                size="md"
              />
            </div>
              <Button className="mt-4 align-self-center" onClick={addContact}>Добавить в контакты</Button>
              {error && <Alert key="danger" variant="danger" className="mt-3">{error}</Alert>}
            </div>
        }
      </Modal.Body>
    </>
  )
}

export default observer(AddContactModal)