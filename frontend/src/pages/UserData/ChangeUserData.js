import React from 'react'
import {Container, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'
import {Link} from 'react-router-dom'

import authStore from '../../stores/authStore'
import ChangeUserDataForm from '../../components/Forms/ChangeUserDataForm'

const ChangeUserData = () => {
  return (
      <Container className="d-flex flex-column justify-content-center w-50" style={{height: '100vh'}}>
        <Row className="mb-3">
          <Link to="/user-data/">К данным</Link>
          <Link to="/">На главную</Link>
        </Row>
        <h1>Изменение данных</h1>
        <h4>Логин: {authStore.user.login}</h4>
        <ChangeUserDataForm />
      </Container>

  )
}

export default observer(ChangeUserData)