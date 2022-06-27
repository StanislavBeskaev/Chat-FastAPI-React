import React from 'react'
import {observer} from 'mobx-react-lite'
import {Badge, Button, ListGroup} from 'react-bootstrap'

import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'
import authStore from '../../../stores/authStore'
import messagesStore from '../../../stores/messagesStore'
import UserAvatar from '../../Avatars/UserAvatar'


const ChatMembers = () => {
  const {members, chatId} = chatMembersModalStore
  const {user} = authStore
  const isChatOwner = user.login === messagesStore.getChatCreator(chatId)

  {/*TODO понять как всегда показывать scroll*/}
  return (
    <div className="d-flex flex-column gap-1">
      <div className="text-primary">
        Участники
      </div>
      <ListGroup
        className="flex-grow-1 overflow-auto"
        style={{maxHeight: 220}}
      >
        {members.map(member =>
          <ListGroup.Item
            key={member.login}
            className="d-flex justify-content-between"
          >
            <div className="d-flex gap-3 align-items-center">
              <UserAvatar login={member.login} size="sm"/>
              {member.login}
              {
                member["is_online"]
                  ? <Badge pill bg="success">online</Badge>
                  : <Badge pill bg="danger">offline</Badge>
              }
            </div>
            {
              isChatOwner && user.login !== member.login && chatId !== 'MAIN'
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
      </ListGroup>
    </div>

  )
}

export default observer(ChatMembers)