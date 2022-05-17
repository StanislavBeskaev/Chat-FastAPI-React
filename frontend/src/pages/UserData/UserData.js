import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Button, Container, Row} from 'react-bootstrap'

import store from '../../stores/store'
import axiosInstance from '../../axios/axios'



const UserData = () => {
  const [file, setFile] = useState(null)
  const [image, setImage] = useState('')
  const [successUpload, setSuccessUpload] = useState(false)

  const uploadFile = async () => {
    if (!file) {
      alert("Укажите файл")
      return
    }
    const formData = new FormData()
    formData.append("file", file, file.name)
    const response = await axiosInstance.post("/user/avatar", formData)
    console.log(response)
    setSuccessUpload(true)
  }

  return (
    <Container>
      <Link to="/">На главную</Link>
      <h1 className="mt-3">Данные пользователя</h1>
      <h2>Логин: {store.user.login}</h2>
      <h2>Имя: {store.user.name}</h2>
      <h2>Фамилия: {store.user.surname}</h2>
      <Link to="/user-data/change">Изменить</Link>
      <Row className="mt-4 mb-3">
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
        <Button onClick={uploadFile}>Отправить файл</Button>
      </Row>
        <span>Выберите файл для аватара</span>
        <input
          type="text"
          value={image}
          onChange={e => setImage(e.target.value)}
          className="mb-3"
        />
      <Row>
        <img src={`http://localhost:8000/api/static/${image}`} alt="Тут будет аватар" />
      </Row>
    </Container>
  )
}

export default UserData