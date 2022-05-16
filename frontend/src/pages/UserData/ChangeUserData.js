import React, {useState} from 'react'
import {Button, Container, Form, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'
import {Link, useHistory} from 'react-router-dom'

import store from '../../stores/store'

const ChangeUserData = () => {
  const [name, setName] = useState(store.user.name)
  const [surname, setSurname] = useState(store.user.surname)

  const history = useHistory()

  const handleSubmit = async e => {
    e.preventDefault()
    await store.changeUserData(name, surname)
    history.push("/user-data/")
  }

  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1>Изменение данных</h1>
      <h4>Логин: {store.user.login}</h4>
      <Form onSubmit={handleSubmit} className="mb-4">
        <Form.Group>
          <Form.Label>Имя</Form.Label>
          <Form.Control
            type="text"
            onChange={e => setName(e.target.value)}
            value={name}/>
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Фамилия</Form.Label>
          <Form.Control
            type="text"
            onChange={e => setSurname(e.target.value)}
            value={surname}
          />
        </Form.Group>
        <Button variant="primary" type="submit" className="me-2">Изменить</Button>
      </Form>
      <Row className="mt-3">
        <Link to="/user-data/">К данным</Link>
        <Link to="/">На главную</Link>
      </Row>
    </Container>
  )
}

export default observer(ChangeUserData)