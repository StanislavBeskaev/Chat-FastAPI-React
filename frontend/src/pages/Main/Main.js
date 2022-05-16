import React from 'react'
import {Button, Container, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'
import {Link} from 'react-router-dom'

import store from '../../stores/store'


const Main = () => {
  return (
    <Container className="mt-3">
      <h2 className="mb-4">Добро пожаловать: {store.user.login}</h2>
      <Button onClick={() => store.callTest()} variant="info">Тест</Button>
      <Button onClick={() => store.logout()} variant="danger" className="ms-3">Выход</Button>
      <Row className="mt-3">
        <Link to="/user-data/">Данные пользователя</Link>
      </Row>
    </Container>
  )
}

export default observer(Main)