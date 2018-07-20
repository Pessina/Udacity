class cleaning:
	
	import re

	"""
	Take as parameter a xml node tag, and returns a dictinoray of this node

	Parameter:
	node: node xml tag

	Return:
	node dictionary object
	"""
	def process_nodes(node):
			# Getting node attributes
	        node_attributes = {
	            'id' : node.attrib ['id'],
	            'user' : node.attrib ['user'],
	            'uid' : node.attrib ['uid'],
	            'version' : node.attrib ['version'],
	            'lat' : node.attrib ['lat'],
	            'lon' : node.attrib ['lon'],
	            'timestamp': node.attrib ['timestamp'],
	            'changeset' : node.attrib ['changeset']
	        }
	        node_tags = []

	        # Getting tags and tags attributes from node
	        for child in node:
	            k = child.attrib ['k'].split(":")

	            tag = {
	                'id' : node_attributes ['id'],
	                'value' : child.attrib ['v'],
	                'type' : 'regular' if len(k)==1 else k[0],
	                'key' : str(':'.join(k[1:])) if len(k) > 1 else child.attrib ['k']
	            }

	            node_tags.append(tag)

	        # Return node object
	        return ({'node': node_attributes, 'node_tags': node_tags}, 'node')

	"""
	Take as parameter a xml way tag, and returns a dictinoray of this way

	Parameter:
	way: way xml tag

	Return:
	way dictionary object
	"""     
	def process_ways(way):
			# Getting way attributes
	        way_attributes = {
	            'id' : way.attrib ['id'],
	            'user' : way.attrib ['user'],
	            'uid' : way.attrib ['uid'],
	            'version' : way.attrib ['version'],
	            'timestamp' : way.attrib ['timestamp'],
	            'changeset' : way.attrib ['changeset']
	        }
	        way_nodes =[]
	        way_tags = []

	        # Getting way tags and nodes, and their attributes
	        for child in way:
	            if child.tag == 'nd':
	                node = {
	                    'id' : way_attributes ['id'],
	                    'node_id' : child.attrib ['ref'],
	                    'position' : len(way_nodes)
	                }
	                way_nodes.append(node)
	            if child.tag == 'tag':
	                k = child.attrib ['k'].split(":")
	                tag = {
	                    'id' : way_attributes ['id'],
	                    'value' : child.attrib ['v'],
	                    'type' : 'regular' if len(k)==1 else k[0],
	                    'key' : str(':'.join(k[1:])) if len(k) > 1 else child.attrib ['k']
	                }
	                way_tags.append(tag)

	        # Return way object
	        return ({'way': way_attributes, 'way_nodes': way_nodes, 'way_tags': way_tags}, 'way')

	"""
	This fuction update misstyping and abreviations tags values
	
	Parameter:
	tag: tag from nodes_tags or ways_tags, to update tag value
	expected: array with expected values for tag value
	regex_dict: regex dictionary with values to update if regex match

	"""
	def update_misstyping_and_abreviations (tag, expected, regex_dict):
	    if tag['key'] == 'street':
	        tag_value_splitted = tag['value'].split(" ")
	        if tag_value_splitted [0] not in expected:
	            for key, values in regex_dict.items():
	                for value in values:
	                    if value.match(tag_value_splitted[0]):
	                        tag_value_splitted [0] = key
	                        tag['value']  = " ".join(tag_value_splitted)

	"""

	Take as parameter a tag to format or remove the cep. 
	
	Parameter:
	tag: tag from nodes_tags or ways_tags, to update tag value
	expected: array with expected values for tag value
	regex_dict: regex dictionary with values to update if regex match

	"""
	def update_cep(tags, non_decimal):
	    
	    for tag in tags:
	        if tag['key'] == 'postcode':
	            cep = tag['value']
	            cep = non_decimal.sub('', cep)
	            if len(cep) != 5 and len(cep) != 8:
	                tags.remove(tag)
	            if len(cep) == 8:
	                cep = cep [0:5] + '-' + cep[5:]
	            tag['value'] = cep
	    return tags