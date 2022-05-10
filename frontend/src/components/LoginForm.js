import React, {useContext, useState} from 'react'
import {Container, Button, InputGroup, FormControl} from 'react-bootstrap'
import {observer} from "mobx-react-lite"

import {Context} from "../index"


const LoginForm = () => {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const {store} = useContext(Context);

  return (
    <Container className="mt-4 mb-3">
      <InputGroup className="w-50 mb-3">
        <FormControl
          placeholder="Логин"
          value={login}
          onChange={e => setLogin(e.target.value)}
        />
        <FormControl
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        <Button onClick={() => store.login(login, password)} variant="success">
          Логин
        </Button>
        <Button onClick={() => store.registration(login, password)} variant="primary">
          Регистрация
        </Button>
      </InputGroup>
    </Container>
  )
}

export default observer(LoginForm)
