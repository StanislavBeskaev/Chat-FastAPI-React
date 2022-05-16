import React from 'react'
import {Container, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'
import {Link} from 'react-router-dom'

import store from '../../stores/store'
import ChangeUserDataForm from '../../components/Forms/ChangeUserDataForm'

const ChangeUserData = () => {
  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1>Изменение данных</h1>
      <h4>Логин: {store.user.login}</h4>
      <ChangeUserDataForm />
      <Row className="mt-3">
        <Link to="/user-data/">К данным</Link>
        <Link to="/">На главную</Link>
      </Row>
    </Container>
  )
}

export default observer(ChangeUserData)