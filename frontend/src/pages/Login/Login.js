import React, {useContext, useEffect} from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import {AuthContext} from '../../context'
import AuthForm from '../../components/AuthForm'


const Login = () => {
  const {store} = useContext(AuthContext)

  useEffect(() => {
    store.setError("")
  }, [])

  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1 className="mb-3">Авторизация</h1>
      <AuthForm
        submitHandler={store.login.bind(store)}
        error={store.error}
        btnText="Авторизоваться"
      />
      <div className="mt-3">
        Нет учётной записи? <Link to="/register">Регистрация</Link>
      </div>
    </Container>
  )
}

export default observer(Login)
