import React from 'react'
import {observer} from 'mobx-react-lite'
import {Badge, Button, ListGroup} from 'react-bootstrap'

import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'
import authStore from '../../../stores/authStore'
import messagesStore from '../../../stores/messagesStore'
import UserAvatar from '../../Avatars/UserAvatar'
import addContactModalStore from '../../../stores/modals/addContactModalStore'


const ChatMembers = () => {
  const {members, chatId} = chatMembersModalStore
  const {user} = authStore
  const chatCreator = messagesStore.getChatCreator(chatId)
  const isMeChatOwner = user.login === chatCreator

  return (
    <div className="d-flex flex-column gap-1">
      <div className="text-primary">
        Участники
      </div>
      <ListGroup
        className="flex-grow-1 overflow-auto"
        style={{maxHeight: 220}}
      >
        {members.map(member => {
          const isMe = member.login === user.login
          const isChatOwner = member.login === chatCreator
          return (
            <ListGroup.Item
              key={member.login}
              className="d-flex justify-content-between align-items-center"
            >
              <div className="d-flex gap-3 align-items-center">
                <div
                  onClick={async () => {
                    if (isMe) return
                    await addContactModalStore.showModalWithLogin(member.login)
                  }}
                  style={{cursor: !isMe ? 'pointer' : null}}
                >
                  <UserAvatar login={member.login} size="sm"/>
                </div>
                {member.login}
                {
                  member["is_online"]
                    ? <Badge pill bg="success">online</Badge>
                    : <Badge pill bg="danger">offline</Badge>
                }
                {
                  isMe
                    ? <Badge pill bg="info">Вы</Badge>
                    : null
                }
                {
                  isChatOwner && chatId !== 'MAIN'
                    ? <Badge pill bg="primary">Создатель</Badge>
                    : null
                }
              </div>
              {
                isMeChatOwner && user.login !== member.login && chatId !== 'MAIN'
                  ? <Button
                    variant="danger"
                    size="sm"
                    onClick={() => chatMembersModalStore.deleteChatMember(member.login)}
                  >
                    X
                  </Button>
                  : null
              }
            </ListGroup.Item>
            )}
        )}
      </ListGroup>
    </div>

  )
}

export default observer(ChatMembers)