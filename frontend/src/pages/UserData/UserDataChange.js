import React from 'react'
import {Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import UserDataChangeForm from '../../components/Forms/UserDataChangeForm'


const UserDataChange = () => {
  const changeUserData = async (name, surname) => {
    await authStore.changeUserData(name, surname)
  }

  return (
      <Container className="d-flex flex-column">
        <h4 className="mb-4">Логин: {authStore.user.login}</h4>
        <UserDataChangeForm
          onSubmit={changeUserData}
          currentName={authStore.user.name}
          currentSurname={authStore.user.surname}
        />
      </Container>
  )
}

export default observer(UserDataChange)
