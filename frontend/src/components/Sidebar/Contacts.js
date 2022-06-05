import React from 'react'
import {ListGroup} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import contactStore from '../../stores/contactStore'
import Contact from './Contact'


const Contacts = () => {
  const {contacts} = contactStore

  if (contacts.length === 0) {
    return <div className="m-3">Тут пока пусто</div>
  }

  return (
    <ListGroup variant="flush" className="m-1">
      {contacts.map(contact => (
        <ListGroup.Item key={contact.login}>
          <Contact
            login={contact.login}
          />
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default observer(Contacts)