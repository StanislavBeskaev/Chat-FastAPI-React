import React, {useState} from 'react'
import {Alert, Button, Form} from 'react-bootstrap'

const AuthForm = ({submitHandler, btnText, error}) => {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    submitHandler(login, password)
  }

  return (
    <>
      {error && <Alert key="danger" variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Логин</Form.Label>
          <Form.Control type="text" required onChange={e => setLogin(e.target.value)}/>
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Пароль</Form.Label>
          <Form.Control type="password" required onChange={e => setPassword(e.target.value)} />
        </Form.Group>
        <Button type="submit" className="me-2">{btnText}</Button>
      </Form>
    </>
  )
}

export default AuthForm