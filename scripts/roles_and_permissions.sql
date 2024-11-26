-- MySQL dump 10.13  Distrib 5.7.28, for Linux (x86_64)
--
-- Host: localhost    Database: smarty
-- ------------------------------------------------------
-- Server version	5.7.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `capability_list`
--

DROP TABLE IF EXISTS `capability_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `capability_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) DEFAULT NULL,
  `create_account` tinyint(1) NOT NULL DEFAULT '0',
  `update_account` tinyint(1) NOT NULL DEFAULT '0',
  `delete_account` tinyint(1) NOT NULL DEFAULT '0',
  `create_role` tinyint(1) NOT NULL DEFAULT '0',
  `delete_role` tinyint(1) NOT NULL DEFAULT '0',
  `get_roles` tinyint(1) NOT NULL DEFAULT '0',
  `set_permissions` tinyint(1) NOT NULL DEFAULT '0',
  `update_billing_info` tinyint(1) NOT NULL DEFAULT '0',
  `view_billing_info` tinyint(1) NOT NULL DEFAULT '0',
  `reset_password` tinyint(1) NOT NULL DEFAULT '0',
  `view_account_info` tinyint(1) NOT NULL DEFAULT '0',
  `add_new_data_source` tinyint(1) NOT NULL DEFAULT '0',
  `delete_data_source` tinyint(1) NOT NULL DEFAULT '0',
  `update_data_source` tinyint(1) NOT NULL DEFAULT '0',
  `view_data_source_information` tinyint(1) NOT NULL DEFAULT '0',
  `add_a_new_label` tinyint(1) NOT NULL DEFAULT '0',
  `merge_by_labelling` tinyint(1) NOT NULL DEFAULT '0',
  `modify_label` tinyint(1) NOT NULL DEFAULT '0',
  `change_to_closed` tinyint(1) NOT NULL DEFAULT '0',
  `modify_severity` tinyint(1) NOT NULL DEFAULT '0',
  `set_severity` tinyint(1) NOT NULL DEFAULT '0',
  `set_to_open` tinyint(1) NOT NULL DEFAULT '0',
  `add_action` tinyint(1) NOT NULL DEFAULT '0',
  `add_alert` tinyint(1) NOT NULL DEFAULT '0',
  `add_solution` tinyint(1) NOT NULL DEFAULT '0',
  `create_new_incident_by_refinement` tinyint(1) NOT NULL DEFAULT '0',
  `delete_action` tinyint(1) NOT NULL DEFAULT '0',
  `delete_alert` tinyint(1) NOT NULL DEFAULT '0',
  `delete_solution` tinyint(1) NOT NULL DEFAULT '0',
  `merge_by_refinement` tinyint(1) NOT NULL DEFAULT '0',
  `modify_action` tinyint(1) NOT NULL DEFAULT '0',
  `modify_alert` tinyint(1) NOT NULL DEFAULT '0',
  `modify_solution` tinyint(1) NOT NULL DEFAULT '0',
  `view_action` tinyint(1) NOT NULL DEFAULT '0',
  `view_alert` tinyint(1) NOT NULL DEFAULT '0',
  `view_solution` tinyint(1) NOT NULL DEFAULT '0',
  `execute_action` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_id` (`role_id`),
  CONSTRAINT `capability_list_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `capability_list`
--

LOCK TABLES `capability_list` WRITE;
/*!40000 ALTER TABLE `capability_list` DISABLE KEYS */;
INSERT INTO `capability_list` VALUES (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),(2,2,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),(3,3,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,1,0,1,1,1,0),(4,4,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0),(5,5,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1,0,0,0,1,0,0,0,1,1,0,1);
/*!40000 ALTER TABLE `capability_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'Administrator','Can do everything'),(2,'Developer','Support level 2'),(3,'Support','Support level 1'),(4,'Guest','Read only'),(5,'Proctor','A new role that just covers what Proctor does');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-02-25 20:17:53
