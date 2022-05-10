import React, {useContext, useEffect} from 'react'

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
    <>
      <h1>Авторизован: {store.isAuth ? 'Да' : 'Нет'}</h1>
      {store.error && <h2>Ошибки: {store.error}</h2>}
      <h2>Пользователь: {store.user.login}</h2>
      <LoginForm />
      <button onClick={() => store.callTest()}>Тест</button>
    </>
  )
}

export default observer(App)
