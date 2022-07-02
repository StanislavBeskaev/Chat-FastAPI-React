import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import UserAvatar from '../../components/Avatars/UserAvatar'
import FileAvatar from '../../components/Avatars/FileAvatar'


const UserData = () => {
  const [file, setFile] = useState(null)
  const [successUpload, setSuccessUpload] = useState(false)

  const uploadFile = async () => {
    if (!file) {
      alert("Выберите файл")
      return
    }
    await authStore.changeAvatar(file)
    setSuccessUpload(true)
  }

  return (
    <div style={{maxWidth: '75%'}} className="p-2 d-flex flex-column flex-grow-1">
      <Link to="/">На главную</Link>
      <h1 className="mt-3">Данные пользователя</h1>
      <h2>Логин: {authStore.user.login}</h2>
      <h2>Имя: {authStore.user.name}</h2>
      <h2>Фамилия: {authStore.user.surname}</h2>
      <Link to="/user-data/change">Изменить</Link>
      <div className="d-flex flex-column align-items-start">
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
        <FileAvatar fileName={authStore.avatarFile} size="lg"/>
      </div>
    </div>
  )
}

export default observer(UserData)