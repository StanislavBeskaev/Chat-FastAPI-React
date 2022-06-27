import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Button, Container, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import UserAvatar from '../../components/Avatars/UserAvatar'


const UserData = () => {
  const [file, setFile] = useState(null)
  const [successUpload, setSuccessUpload] = useState(false)

  const uploadFile = async () => {
    if (!file) {
      alert("Укажите файл")
      return
    }
    await authStore.saveAvatar(file)
    setSuccessUpload(true)
  }

  return (
    <Container>
      <Link to="/">На главную</Link>
      <h1 className="mt-3">Данные пользователя</h1>
      <h2>Логин: {authStore.user.login}</h2>
      <h2>Имя: {authStore.user.name}</h2>
      <h2>Фамилия: {authStore.user.surname}</h2>
      <Link to="/user-data/change">Изменить</Link>
      <Row className="mt-5 mb-3 w-50">
        <h5>Изменить аватар</h5>
        <input
          type="file"
          id="file"
          onChange={e => {
            setFile(e.target.files[0])
            console.log("file change")
            setSuccessUpload(false)
          }}
          className="mb-3"
        />
        {
          successUpload
            ? <span className="text-success">Файл загружен</span>
            : <span className="text-danger">Отправьте файл</span>
        }
        <Button onClick={uploadFile} className="mb-3">Отправить файл</Button>
        <UserAvatar login="admin" size="lg" />
      </Row>
    </Container>
  )
}

export default observer(UserData)