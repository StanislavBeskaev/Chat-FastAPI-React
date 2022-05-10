import React, {useContext} from 'react'
import {Button, Container} from 'react-bootstrap'
import {Context} from '../../../index'
import {observer} from 'mobx-react-lite'


const MainPage = () => {
  const {store} = useContext(Context)
  return (
    <Container className="mt-3">
      <h2>Пользователь: {store.user.login}</h2>
      <Button onClick={() => store.callTest()} variant="info">Тест</Button>
    </Container>
  )
}

export default observer(MainPage)