import React, {useContext, useEffect} from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import {AuthContext} from '../../context'
import AuthForm from '../../components/AuthForm'


const Register = () => {
  const {store} = useContext(AuthContext)

  useEffect(() => {
    store.setError("")
  }, [])

  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1 className="mb-3">Регистрация</h1>
      <AuthForm
        submitHandler={store.registration.bind(store)}
        error={store.error}
        btnText="Зарегистрироваться"
      />
      <Link to="/login" className="mt-3">Авторизация</Link>
    </Container>
  )
}

export default observer(Register)