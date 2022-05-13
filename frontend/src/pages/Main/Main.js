import React, {useContext} from 'react'
import {Button, Container} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import {AuthContext} from '../../context'


const Main = () => {
  const {store} = useContext(AuthContext)
  return (
    <Container className="mt-3">
      <h2 className="mb-4">Добро пожаловать: {store.user.login}</h2>
      <Button onClick={() => store.callTest()} variant="info">Тест</Button>
      <Button onClick={() => store.logout()} variant="danger" className="ms-3">Выход</Button>
    </Container>
  )
}

export default observer(Main)