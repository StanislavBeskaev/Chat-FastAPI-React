import React from 'react'
import {observer} from 'mobx-react-lite'

import {Button, ListGroup} from 'react-bootstrap'
import contactStore from '../../../stores/contactStore'
import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'


const ContactsOutsideChat = () => {
  const {contacts} = contactStore
  const {members} = chatMembersModalStore

  const membersLogins = members.map(member => member.login)
  const contactsOutside = contacts.filter(contact => !membersLogins.includes(contact.login))

  if (contactsOutside.length === 0) {
    return <h6 className="text-primary">Все ваши контакты есть в этом чате</h6>
  }

  return (
    <div className="d-flex flex-column gap-1">
      <div className="text-primary">
        Контакты вне чата
      </div>
      <ListGroup
        className="flex-grow-1 overflow-auto"
        style={{maxHeight: 220}}
      >
        {contactsOutside.map(contact =>
          <ListGroup.Item
            key={contact.login}
            className="d-flex justify-content-between"
          >
            <div>
              {contactStore.getDisplayName(contact.login)}
            </div>
            <Button
              size="sm"
              variant="success"
              onClick={async () => chatMembersModalStore.addChatMember(contact.login)}
            >
              +
            </Button>
          </ListGroup.Item>
        )}
      </ListGroup>
    </div>
  )
}

export default observer(ContactsOutsideChat)