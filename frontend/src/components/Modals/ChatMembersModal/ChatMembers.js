import React from 'react'
import {observer} from 'mobx-react-lite'
import {Badge, ListGroup} from 'react-bootstrap'

import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'


const ChatMembers = () => {
  const {members} = chatMembersModalStore

  {/*TODO понять как всегда показывать scroll*/}
  return (
    <div className="d-flex flex-column gap-1">
      <div className="text-primary">
        Участники
      </div>
      <ListGroup
        className="flex-grow-1 overflow-auto"
        style={{maxHeight: 250}}
      >
        {members.map(member =>
          <ListGroup.Item
            key={member.login}
            className="d-flex gap-3"
          >
            <div>
              {member.login}
            </div>
            {
              member["is_online"]
                ? <Badge pill bg="success">online</Badge>
                : <Badge pill bg="danger">offline</Badge>
            }
          </ListGroup.Item>
        )}
      </ListGroup>
    </div>

  )
}

export default observer(ChatMembers)