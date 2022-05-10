import React, {useContext, useState} from 'react'
import {Container, Form, Button, Alert} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import {Context} from "../../../index"


const LoginPage= () => {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const {store} = useContext(Context);

  function handleSubmit(e) {
    e.preventDefault()
    store.login(login, password)
  }

  return (
    <Container className="justify-content-center d-flex flex-column w-75" style={{height: '100vh'}}>
      {store.error && <Alert key="danger" variant="danger">{store.error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Логин</Form.Label>
          <Form.Control type="text" required onChange={e => setLogin(e.target.value)}/>
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Пароль</Form.Label>
          <Form.Control type="password" required onChange={e => setPassword(e.target.value)} />
        </Form.Group>
        <Button type="submit" className="me-2">Авторизоваться</Button>
      </Form>
    </Container>
  )
}

export default observer(LoginPage)
