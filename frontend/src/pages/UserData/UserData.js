import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import FileAvatar from '../../components/Avatars/FileAvatar'
import logMessages from '../../log'


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
    <div style={{maxWidth: '75%'}} className="ps-4 d-flex flex-column flex-grow-1">
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
            logMessages("file change")
            setSuccessUpload(false)
          }}
          className="mb-3"
        />
        {
          successUpload
            ? <span className="text-success mb-1">Аватар изменён</span>
            : null
        }
        {
          file && !successUpload
            ? <Button onClick={uploadFile} className="mb-3">Отправить файл</Button>
            : null
        }
        <FileAvatar fileName={authStore.avatarFile} size="md"/>
      </div>
    </div>
  )
}

export default observer(UserData)