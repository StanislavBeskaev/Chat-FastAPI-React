import React, {useState} from 'react'
import {Button, Container} from 'react-bootstrap'

import authStore from '../../stores/authStore'
import FileAvatar from '../../components/Avatars/FileAvatar'


const AvatarChange = () => {
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
    <Container className="d-flex flex-row align-items-center gap-4">
      <div>
        <FileAvatar fileName={authStore.avatarFile} size="md"/>
      </div>
      <div className="d-flex flex-column">
        <h5 className="mt-4">Изменить аватар</h5>
        <input
          type="file"
          id="file"
          onChange={e => {
            setFile(e.target.files[0])
            setSuccessUpload(false)
          }}
          className="mb-4"
        />
        {
          successUpload
            ? <span className="text-success mb-1">Аватар изменён</span>
            : null
        }
        {
          file && !successUpload
            ? <Button onClick={uploadFile} className="mb-3 align-self-start">Отправить файл</Button>
            : null
        }
      </div>

    </Container>
  )
}

export default AvatarChange