import React, {useContext} from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'

import {AuthContext} from '../../context'

const UserData = () => {
  const {store: {user}} = useContext(AuthContext)
  return (
    <Container>
      <Link to="/">На главную</Link>
      <h1 className="mt-3">Данные пользователя</h1>
      <h2>Логин: {user.login}</h2>
      <h2>Имя: {user.name}</h2>
      <h2>Фамилия: {user.surname}</h2>
      <Link to="/user-data/change">Изменить</Link>
    </Container>
  )
}

export default UserData