import React, {useContext, useEffect} from 'react'
import {Button, Container} from 'react-bootstrap'

import {observer} from "mobx-react-lite"
import {Context} from "./index"
import LoginForm from './components/LoginForm'

function App() {
  const {store} = useContext(Context)

  useEffect(() => {
    if (localStorage.getItem('token')) {
      store.checkAuth()
    }
  }, [])

  return (
    <Container className="mt-3">
      <h1>Авторизован: {store.isAuth ? 'Да' : 'Нет'}</h1>
      {store.error && <h2>Ошибки: {store.error}</h2>}
      <h2>Пользователь: {store.user.login}</h2>
      <LoginForm />
      <Button onClick={() => store.callTest()} variant="info">Тест</Button>
    </Container>
  )
}

export default observer(App)
