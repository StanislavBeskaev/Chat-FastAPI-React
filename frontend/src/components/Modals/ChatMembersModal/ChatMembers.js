import React from 'react'
import {observer} from 'mobx-react-lite'
import {ListGroup} from 'react-bootstrap'

import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'
import authStore from '../../../stores/authStore'
import messagesStore from '../../../stores/messagesStore'
import ChatMember from './ChatMember'


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
          return <ChatMember
            member={member}
            isMe={isMe}
            isChatOwner={isChatOwner}
            chatId={chatId}
            canDeleteChatMember={isMeChatOwner && user.login !== member.login && chatId !== 'MAIN'}
          />}
        )}
      </ListGroup>
    </div>

  )
}

export default observer(ChatMembers)