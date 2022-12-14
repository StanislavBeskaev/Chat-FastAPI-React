import React, {useEffect} from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import LoginForm from '../../components/Forms/LoginForm'
import authStore from '../../stores/authStore'


const Login = () => {
  useEffect(() => {
    authStore.setError("")
  }, [])

  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1 className="mb-3">Авторизация</h1>
      <LoginForm
        submitHandler={authStore.login.bind(authStore)}
        error={authStore.error}
        btnText="Авторизоваться"
      />
      <div className="mt-3">
        Нет учётной записи? <Link to="/register">Регистрация</Link>
      </div>
    </Container>
  )
}

export default observer(Login)
