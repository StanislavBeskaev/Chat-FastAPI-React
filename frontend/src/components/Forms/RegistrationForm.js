import React, {useState} from 'react'
import {Alert, Button, Form} from 'react-bootstrap'

import SimpleInput from '../UI/Inputs/SimpleInput'

const RegistrationForm = ({submitHandler, btnText, error}) => {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [surname, setSurname] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    submitHandler(login, password, name, surname)
  }

  return (
    <>
      {error && <Alert key="danger" variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <SimpleInput
          label="Логин"
          type="text"
          required={true}
          onChange={e => setLogin(e.target.value)}
        />
        <SimpleInput
          label="Пароль"
          type="password"
          required={true}
          onChange={e => setPassword(e.target.value)}
        />
        <SimpleInput
          label="Имя"
          type="text"
          required={false}
          onChange={e => setName(e.target.value)}
        />
        <SimpleInput
          label="Фамилия"
          type="text"
          required={false}
          onChange={e => setSurname(e.target.value)}
        />
        <Button type="submit" className="me-2">{btnText}</Button>
      </Form>
    </>
  )
}

export default RegistrationForm