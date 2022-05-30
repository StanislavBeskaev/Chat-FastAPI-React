import React, {useEffect, useState} from 'react'
import {Button, Modal} from 'react-bootstrap'

import modalsStore from '../../stores/modalsStore'
import Loader from '../UI/Loader/Loader'
import Avatar from '../Avatars/Avatar'

const AddContactModal = () => {
  const [loading, setLoading] = useState(true)
  const {addContactLogin: login} = modalsStore

  useEffect(() => {
    modalsStore.loadUserInfo()
      .catch(e => console.log(`Не удалось загрузить информацию о пользователе: ${login}`, e))
      .finally(() => setLoading(false))
  }, [] )

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
                <li>Имя: {modalsStore.addContactUserInfo.name}</li>
                <li>Фамилия: {modalsStore.addContactUserInfo.surname}</li>
              </ul>
              <Avatar
                fileName={modalsStore.addContactUserInfo.avatar_file}
                size="md"
              />
            </div>
              <Button className="mt-4 align-self-center">Добавить в контакты</Button>
            </div>

        }
      </Modal.Body>
    </>
  )
}

export default AddContactModal