import React, {useContext, useState} from 'react'
import {observer} from "mobx-react-lite"

import {Context} from "../index"


const LoginForm = () => {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const {store} = useContext(Context);

  return (
    <div>
      <input
        onChange={e => setLogin(e.target.value)}
        value={login}
        type="text"
        placeholder='Логин'
      />
      <input
        onChange={e => setPassword(e.target.value)}
        value={password}
        type="password"
        placeholder='Пароль'
      />
      <button onClick={() => store.login(login, password)}>
        Логин
      </button>
      <button onClick={() => store.registration(login, password)}>
        Регистрация
      </button>
    </div>
  )
}

export default observer(LoginForm)
