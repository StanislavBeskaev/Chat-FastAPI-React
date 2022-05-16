import React from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'

import store from '../../stores/store'



const UserData = () => {
  return (
    <Container>
      <Link to="/">На главную</Link>
      <h1 className="mt-3">Данные пользователя</h1>
      <h2>Логин: {store.user.login}</h2>
      <h2>Имя: {store.user.name}</h2>
      <h2>Фамилия: {store.user.surname}</h2>
      <Link to="/user-data/change">Изменить</Link>
    </Container>
  )
}

export default UserData