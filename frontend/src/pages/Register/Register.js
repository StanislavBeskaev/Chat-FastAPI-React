import React, {useEffect} from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import LoginForm from '../../components/Forms/LoginForm'
import store from '../../stores/store'


const Register = () => {
  useEffect(() => {
    store.setError("")
  }, [])

  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1 className="mb-3">Регистрация</h1>
      <LoginForm
        submitHandler={store.registration.bind(store)}
        error={store.error}
        btnText="Зарегистрироваться"
      />
      <Link to="/login" className="mt-3">Авторизация</Link>
    </Container>
  )
}

export default observer(Register)