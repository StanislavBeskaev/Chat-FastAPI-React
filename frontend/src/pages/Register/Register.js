import React, {useEffect} from 'react'
import {Link} from 'react-router-dom'
import {Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import RegistrationForm from '../../components/Forms/RegistrationForm'
import authStore from '../../stores/authStore'


const Register = () => {
  useEffect(() => {
    authStore.setError("")
  }, [])

  return (
    <Container className="justify-content-center d-flex flex-column w-50" style={{height: '100vh'}}>
      <h1 className="mb-3">Регистрация</h1>
      <RegistrationForm
        submitHandler={authStore.registration.bind(authStore)}
        error={authStore.error}
        btnText="Зарегистрироваться"
      />
      <Link to="/login" className="mt-3">Авторизация</Link>
    </Container>
  )
}

export default observer(Register)